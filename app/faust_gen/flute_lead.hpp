/* ------------------------------------------------------------
name: "flute_lead"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FluteLead -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FluteLead_H__
#define  __FluteLead_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FluteLead
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

class FluteLeadSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec2[2];
	
  public:
	
	int getNumInputsFluteLeadSIG0() {
		return 0;
	}
	int getNumOutputsFluteLeadSIG0() {
		return 1;
	}
	
	void instanceInitFluteLeadSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec2[l5] = 0;
		}
	}
	
	void fillFluteLeadSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec2[0] = (iVec2[1] + iRec2[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec2[0]));
			iVec2[1] = iVec2[0];
			iRec2[1] = iRec2[0];
		}
	}

};

static FluteLeadSIG0* newFluteLeadSIG0() { return (FluteLeadSIG0*)new FluteLeadSIG0(); }
static void deleteFluteLeadSIG0(FluteLeadSIG0* dsp) { delete dsp; }

static float ftbl0FluteLeadSIG0[65536];
static float FluteLead_faustpower2_f(float value) {
	return value * value;
}

class FluteLead : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	FAUSTFLOAT fHslider0;
	float fConst3;
	float fConst4;
	float fRec4[2];
	float fConst5;
	float fConst6;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst7;
	float fRec3[2];
	float fConst8;
	float fRec5[2];
	float fConst9;
	float fRec6[2];
	float fConst10;
	int iRec9[2];
	FAUSTFLOAT fHslider3;
	float fRec8[3];
	float fVec3[2];
	float fConst12;
	float fConst13;
	float fRec7[2];
	FAUSTFLOAT fHslider4;
	
 public:
	FluteLead() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FluteLead -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "flute_lead.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "flute_lead");
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
		FluteLeadSIG0* sig0 = newFluteLeadSIG0();
		sig0->instanceInitFluteLeadSIG0(sample_rate);
		sig0->fillFluteLeadSIG0(65536, ftbl0FluteLeadSIG0);
		deleteFluteLeadSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.15f * fConst0);
		float fConst2 = std::max<float>(1.0f, 0.1f * fConst0);
		fConst3 = 0.15f / fConst2;
		fConst4 = 5.2f / fConst0;
		fConst5 = 1.0f / fConst2;
		fConst6 = 1.0f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst7 = 3.0f / fConst0;
		fConst8 = 2.0f / fConst0;
		fConst9 = 1.0f / fConst0;
		fConst10 = 15.707963f / fConst0;
		float fConst11 = 1.0f / std::tan(16336.282f / fConst0);
		fConst12 = 1.0f - fConst11;
		fConst13 = 1.0f / (fConst11 + 1.0f);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.045f);
		fHslider1 = FAUSTFLOAT(0.012f);
		fHslider2 = FAUSTFLOAT(4.4e+02f);
		fHslider3 = FAUSTFLOAT(0.09f);
		fHslider4 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec4[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec3[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec5[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec6[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			iRec9[l10] = 0;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec8[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fVec3[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec7[l13] = 0.0f;
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
	
	virtual FluteLead* clone() {
		return new FluteLead();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("flute_lead");
		ui_interface->addHorizontalSlider("air", &fHslider3, FAUSTFLOAT(0.09f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("attack", &fHslider0, FAUSTFLOAT(0.045f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.4f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("vibrato", &fHslider1, FAUSTFLOAT(0.012f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.04f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = 1.0f / fSlow2;
		float fSlow4 = float(fHslider1);
		float fSlow5 = float(fHslider2);
		float fSlow6 = fConst7 * fSlow5;
		float fSlow7 = fConst8 * fSlow5;
		float fSlow8 = fConst9 * fSlow5;
		float fSlow9 = fConst10 * fSlow5;
		float fSlow10 = 4.656613e-10f * float(fHslider3);
		float fSlow11 = float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			int iTemp1 = 1 - iVec0[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fConst4 + fRec4[1]);
			fRec4[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = fSlow4 * std::max<float>(0.0f, std::min<float>(fConst6 * fRec1[0], 1.0f) - fConst5 * fTemp0) * ftbl0FluteLeadSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] + 1.0f;
			float fTemp4 = ((iTemp1) ? 0.0f : fRec3[1] + fSlow6 * fTemp3);
			fRec3[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = ((iTemp1) ? 0.0f : fRec5[1] + fSlow7 * fTemp3);
			fRec5[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp1) ? 0.0f : fRec6[1] + fSlow8 * fTemp3);
			fRec6[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = std::tan(fSlow9 * fTemp3);
			float fTemp8 = 1.0f / fTemp7;
			float fTemp9 = (fTemp8 + 0.8333333f) / fTemp7 + 1.0f;
			iRec9[0] = 1103515245 * iRec9[1] + 12345;
			fRec8[0] = fSlow10 * float(iRec9[0]) - (fRec8[2] * ((fTemp8 + -0.8333333f) / fTemp7 + 1.0f) + 2.0f * fRec8[1] * (1.0f - 1.0f / FluteLead_faustpower2_f(fTemp7))) / fTemp9;
			float fTemp10 = (fRec8[0] - fRec8[2]) / (fTemp7 * fTemp9);
			fVec3[0] = fTemp10;
			fRec7[0] = -(fConst13 * (fConst12 * fRec7[1] - (fTemp10 + fVec3[1])));
			float fTemp11 = fSlow11 * (fRec7[0] + 0.8f * (ftbl0FluteLeadSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] + 0.18f * ftbl0FluteLeadSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec5[0]), 65535))] + 0.05f * ftbl0FluteLeadSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec3[0]), 65535))])) * std::max<float>(0.0f, std::min<float>(fSlow3 * fRec1[0], std::max<float>(fConst3 * (fSlow2 - fRec1[0]) + 1.0f, 0.85f)) * (1.0f - fConst1 * fTemp0));
			output0[i0] = FAUSTFLOAT(fTemp11);
			output1[i0] = FAUSTFLOAT(fTemp11);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec4[1] = fRec4[0];
			fRec3[1] = fRec3[0];
			fRec5[1] = fRec5[0];
			fRec6[1] = fRec6[0];
			iRec9[1] = iRec9[0];
			fRec8[2] = fRec8[1];
			fRec8[1] = fRec8[0];
			fVec3[1] = fVec3[0];
			fRec7[1] = fRec7[0];
		}
	}

};

#endif
