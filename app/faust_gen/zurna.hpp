/* ------------------------------------------------------------
name: "zurna"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Zurna -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Zurna_H__
#define  __Zurna_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Zurna
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

class ZurnaSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec5[2];
	
  public:
	
	int getNumInputsZurnaSIG0() {
		return 0;
	}
	int getNumOutputsZurnaSIG0() {
		return 1;
	}
	
	void instanceInitZurnaSIG0(int sample_rate) {
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iVec2[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec5[l5] = 0;
		}
	}
	
	void fillZurnaSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec5[0] = (iVec2[1] + iRec5[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec5[0]));
			iVec2[1] = iVec2[0];
			iRec5[1] = iRec5[0];
		}
	}

};

static ZurnaSIG0* newZurnaSIG0() { return (ZurnaSIG0*)new ZurnaSIG0(); }
static void deleteZurnaSIG0(ZurnaSIG0* dsp) { delete dsp; }

static float Zurna_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0ZurnaSIG0[65536];

class Zurna : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fRec1[2];
	FAUSTFLOAT fHslider1;
	float fConst1;
	FAUSTFLOAT fHslider2;
	float fConst2;
	FAUSTFLOAT fHslider3;
	float fConst3;
	float fRec6[2];
	FAUSTFLOAT fHslider4;
	FAUSTFLOAT fHslider5;
	float fRec3[2];
	FAUSTFLOAT fHslider6;
	FAUSTFLOAT fHslider7;
	float fRec7[3];
	float fRec2[3];
	FAUSTFLOAT fHslider8;
	
 public:
	Zurna() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Zurna -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "zurna.dsp");
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
		m->declare("name", "zurna");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		ZurnaSIG0* sig0 = newZurnaSIG0();
		sig0->instanceInitZurnaSIG0(sample_rate);
		sig0->fillZurnaSIG0(65536, ftbl0ZurnaSIG0);
		deleteZurnaSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 0.1f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst2 = 3.1415927f / fConst0;
		fConst3 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.12f);
		fHslider1 = FAUSTFLOAT(0.02f);
		fHslider2 = FAUSTFLOAT(7e+03f);
		fHslider3 = FAUSTFLOAT(5.5f);
		fHslider4 = FAUSTFLOAT(0.006f);
		fHslider5 = FAUSTFLOAT(4.4e+02f);
		fHslider6 = FAUSTFLOAT(1.6f);
		fHslider7 = FAUSTFLOAT(1.6e+03f);
		fHslider8 = FAUSTFLOAT(0.8f);
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
			fRec6[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec3[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec2[l9] = 0.0f;
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
	
	virtual Zurna* clone() {
		return new Zurna();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("zurna");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.02f), FAUSTFLOAT(0.002f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bright", &fHslider2, FAUSTFLOAT(7e+03f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("buzz", &fHslider6, FAUSTFLOAT(1.6f), FAUSTFLOAT(1.0f), FAUSTFLOAT(4.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider5, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(1.2e+02f), FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider8, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("nasal", &fHslider7, FAUSTFLOAT(1.6e+03f), FAUSTFLOAT(8e+02f), FAUSTFLOAT(3.5e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("release", &fHslider0, FAUSTFLOAT(0.12f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("vibrate", &fHslider3, FAUSTFLOAT(5.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider4, FAUSTFLOAT(0.006f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.025f), FAUSTFLOAT(0.0001f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow4 = 1.0f / fSlow3;
		float fSlow5 = std::tan(fConst2 * float(fHslider2));
		float fSlow6 = 2.0f * (1.0f - 1.0f / Zurna_faustpower2_f(fSlow5));
		float fSlow7 = 1.0f / fSlow5;
		float fSlow8 = (fSlow7 + -1.4142135f) / fSlow5 + 1.0f;
		float fSlow9 = (fSlow7 + 1.4142135f) / fSlow5 + 1.0f;
		float fSlow10 = 1.0f / fSlow9;
		float fSlow11 = fConst3 * float(fHslider3);
		float fSlow12 = float(fHslider4);
		float fSlow13 = float(fHslider5);
		float fSlow14 = float(fHslider6);
		float fSlow15 = std::tan(fConst2 * float(fHslider7));
		float fSlow16 = 2.0f * (1.0f - 1.0f / Zurna_faustpower2_f(fSlow15));
		float fSlow17 = 1.0f / fSlow15;
		float fSlow18 = (fSlow17 + -0.45454547f) / fSlow15 + 1.0f;
		float fSlow19 = (fSlow17 + 0.45454547f) / fSlow15 + 1.0f;
		float fSlow20 = 1.0f / fSlow19;
		float fSlow21 = 0.7f / (fSlow15 * fSlow19);
		float fSlow22 = 0.45f * (float(fHslider8) / fSlow9);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			float fTemp0 = ((1 - iVec0[1]) ? 0.0f : fSlow11 + fRec6[1]);
			fRec6[0] = fTemp0 - std::floor(fTemp0);
			float fTemp1 = std::max<float>(1.1920929e-07f, std::fabs(fSlow13 * (fSlow12 * ftbl0ZurnaSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec6[0]), 65535))] + 1.0f)));
			float fTemp2 = fRec3[1] + fConst3 * fTemp1;
			float fTemp3 = fTemp2 + -1.0f;
			int iTemp4 = fTemp3 < 0.0f;
			fRec3[0] = ((iTemp4) ? fTemp2 : fTemp3);
			float fRec4 = ((iTemp4) ? fTemp2 : fTemp2 + fTemp3 * (1.0f - fConst0 / fTemp1));
			float fTemp5 = tanhf(fSlow14 * (2.0f * fRec4 + -1.0f));
			fRec7[0] = fTemp5 - fSlow20 * (fSlow18 * fRec7[2] + fSlow16 * fRec7[1]);
			fRec2[0] = fSlow21 * (fRec7[0] - fRec7[2]) + 0.4f * fTemp5 - fSlow10 * (fSlow8 * fRec2[2] + fSlow6 * fRec2[1]);
			float fTemp6 = fSlow22 * (fRec2[2] + fRec2[0] + 2.0f * fRec2[1]) * std::max<float>(0.0f, std::min<float>(fSlow4 * fRec1[0], std::max<float>(fConst1 * (fSlow3 - fRec1[0]) + 1.0f, 0.9f)) * (1.0f - fSlow2 * float(iRec0[0])));
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec6[1] = fRec6[0];
			fRec3[1] = fRec3[0];
			fRec7[2] = fRec7[1];
			fRec7[1] = fRec7[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
