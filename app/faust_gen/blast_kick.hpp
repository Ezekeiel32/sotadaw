/* ------------------------------------------------------------
name: "blast_kick"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn BlastKick -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __BlastKick_H__
#define  __BlastKick_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS BlastKick
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class BlastKickSIG0 {
	
  private:
	
	int iVec1[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsBlastKickSIG0() {
		return 0;
	}
	int getNumOutputsBlastKickSIG0() {
		return 1;
	}
	
	void instanceInitBlastKickSIG0(int sample_rate) {
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iVec1[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec2[l4] = 0;
		}
	}
	
	void fillBlastKickSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec1[0] = 1;
			iRec2[0] = (iVec1[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec1[1] = iVec1[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static BlastKickSIG0* newBlastKickSIG0() { return (BlastKickSIG0*)new BlastKickSIG0(); }
static void deleteBlastKickSIG0(BlastKickSIG0* dsp) { delete dsp; }

static float BlastKick_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0BlastKickSIG0[65536];

class BlastKick : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	int iRec1[2];
	float fRec0[3];
	float fConst8;
	float fConst9;
	float fRec3[2];
	float fConst10;
	float fRec4[2];
	FAUSTFLOAT fButton0;
	float fVec2[2];
	int iRec5[2];
	float fConst11;
	float fConst12;
	float fConst13;
	FAUSTFLOAT fHslider0;
	float fConst14;
	float fConst15;
	FAUSTFLOAT fHslider1;
	float fConst16;
	float fConst17;
	float fConst18;
	FAUSTFLOAT fHslider2;
	float fConst19;
	float fRec6[2];
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	
 public:
	BlastKick() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn BlastKick -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "blast_kick.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "blast_kick");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		BlastKickSIG0* sig0 = newBlastKickSIG0();
		sig0->instanceInitBlastKickSIG0(sample_rate);
		sig0->fillBlastKickSIG0(65536, ftbl0BlastKickSIG0);
		deleteBlastKickSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(5026.5483f / fConst0);
		float fConst2 = BlastKick_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = 1.0f / (fConst2 * fConst6);
		fConst9 = 4.7e+03f / fConst0;
		fConst10 = 3.3e+03f / fConst0;
		fConst11 = std::max<float>(1.0f, 0.0002f * fConst0);
		fConst12 = 1.0f / fConst11;
		fConst13 = 1.0f / std::max<float>(1.0f, 0.005f * fConst0);
		fConst14 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst15 = 1.0f / fConst14;
		fConst16 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst17 = 1.0f / fConst16;
		fConst18 = 1.0f / std::max<float>(1.0f, 0.018f * fConst0);
		fConst19 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(1.0f);
		fHslider1 = FAUSTFLOAT(0.09f);
		fHslider2 = FAUSTFLOAT(5e+01f);
		fHslider3 = FAUSTFLOAT(3.0f);
		fHslider4 = FAUSTFLOAT(0.95f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec0[l2] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec3[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec2[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec5[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual BlastKick* clone() {
		return new BlastKick();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("blast_kick");
		ui_interface->addHorizontalSlider("click", &fHslider0, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider1, FAUSTFLOAT(0.09f), FAUSTFLOAT(0.04f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("drive", &fHslider3, FAUSTFLOAT(3.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(5e+01f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(3e+02f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.95f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = 0.7f * float(fHslider0);
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow3 = fConst19 * float(fHslider2);
		float fSlow4 = float(fHslider3);
		float fSlow5 = 0.62f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			iRec1[0] = 1103515245 * iRec1[1] + 12345;
			fRec0[0] = 4.656613e-10f * float(iRec1[0]) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			int iTemp0 = 1 - iVec0[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fConst9 + fRec3[1]);
			fRec3[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = ((iTemp0) ? 0.0f : fConst10 + fRec4[1]);
			fRec4[0] = fTemp2 - std::floor(fTemp2);
			fVec2[0] = fSlow0;
			iRec5[0] = (fSlow0 > fVec2[1]) + (fSlow0 <= fVec2[1]) * (iRec5[1] + (iRec5[1] > 0));
			float fTemp3 = float(iRec5[0]);
			float fTemp4 = ((iTemp0) ? 0.0f : fRec6[1] + fSlow3 * (7.0f * std::max<float>(0.0f, std::min<float>(fConst17 * fTemp3, fConst18 * (fConst16 - fTemp3) + 1.0f)) + 1.0f));
			fRec6[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = fSlow5 * tanhf(fSlow4 * (ftbl0BlastKickSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst15 * fTemp3, fSlow2 * (fConst14 - fTemp3) + 1.0f)) + fSlow1 * std::max<float>(0.0f, std::min<float>(fConst12 * fTemp3, fConst13 * (fConst11 - fTemp3) + 1.0f)) * (0.5f * (ftbl0BlastKickSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] + 0.6f * ftbl0BlastKickSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))]) + fConst8 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]))));
			output0[i0] = FAUSTFLOAT(fTemp5);
			output1[i0] = FAUSTFLOAT(fTemp5);
			iVec0[1] = iVec0[0];
			iRec1[1] = iRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec3[1] = fRec3[0];
			fRec4[1] = fRec4[0];
			fVec2[1] = fVec2[0];
			iRec5[1] = iRec5[0];
			fRec6[1] = fRec6[0];
		}
	}

};

#endif
