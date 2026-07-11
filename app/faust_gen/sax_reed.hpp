/* ------------------------------------------------------------
name: "sax_reed"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn SaxReed -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __SaxReed_H__
#define  __SaxReed_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS SaxReed
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

class SaxReedSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec8[2];
	
  public:
	
	int getNumInputsSaxReedSIG0() {
		return 0;
	}
	int getNumOutputsSaxReedSIG0() {
		return 1;
	}
	
	void instanceInitSaxReedSIG0(int sample_rate) {
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iVec2[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			iRec8[l9] = 0;
		}
	}
	
	void fillSaxReedSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec8[0] = (iVec2[1] + iRec8[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec8[0]));
			iVec2[1] = iVec2[0];
			iRec8[1] = iRec8[0];
		}
	}

};

static SaxReedSIG0* newSaxReedSIG0() { return (SaxReedSIG0*)new SaxReedSIG0(); }
static void deleteSaxReedSIG0(SaxReedSIG0* dsp) { delete dsp; }

static float SaxReed_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0SaxReedSIG0[65536];

class SaxReed : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	float fConst3;
	int iRec1[2];
	FAUSTFLOAT fHslider0;
	float fRec2[2];
	FAUSTFLOAT fHslider1;
	float fConst4;
	FAUSTFLOAT fHslider2;
	float fConst5;
	int iRec4[2];
	float fRec3[3];
	FAUSTFLOAT fHslider3;
	float fConst7;
	float fConst9;
	float fConst11;
	FAUSTFLOAT fHslider4;
	float fRec5[3];
	float fConst12;
	float fConst13;
	float fRec9[2];
	float fConst14;
	float fRec12[2];
	float fConst15;
	float fConst16;
	FAUSTFLOAT fHslider5;
	float fConst17;
	FAUSTFLOAT fHslider6;
	float fConst18;
	float fRec10[2];
	float fRec13[2];
	float fVec3[2];
	int IOTA0;
	float fVec4[4096];
	float fConst19;
	float fConst20;
	float fRec14[2];
	float fVec5[2];
	float fConst21;
	float fConst22;
	float fConst23;
	float fRec7[2];
	float fRec6[3];
	float fConst24;
	float fRec16[3];
	float fConst25;
	float fRec17[3];
	float fConst26;
	float fRec18[3];
	float fConst27;
	float fRec19[3];
	FAUSTFLOAT fHslider7;
	
 public:
	SaxReed() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn SaxReed -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "sax_reed.dsp");
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
		m->declare("name", "sax_reed");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
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
		SaxReedSIG0* sig0 = newSaxReedSIG0();
		sig0->instanceInitSaxReedSIG0(sample_rate);
		sig0->fillSaxReedSIG0(65536, ftbl0SaxReedSIG0);
		deleteSaxReedSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.02f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 1.0f / std::max<float>(1.0f, 0.22f * fConst0);
		fConst4 = 0.18f / std::max<float>(1.0f, 0.12f * fConst0);
		fConst5 = 3.1415927f / fConst0;
		float fConst6 = std::tan(8168.141f / fConst0);
		fConst7 = 2.0f * (1.0f - 1.0f / SaxReed_faustpower2_f(fConst6));
		float fConst8 = 1.0f / fConst6;
		fConst9 = (fConst8 + -0.6666667f) / fConst6 + 1.0f;
		float fConst10 = (fConst8 + 0.6666667f) / fConst6 + 1.0f;
		fConst11 = 1.0f / fConst10;
		fConst12 = 1.0f / (fConst6 * fConst10);
		fConst13 = 52.0f / fConst0;
		fConst14 = 5.4f / fConst0;
		fConst15 = 1.0f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst16 = 1.0f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst17 = 1.0f / std::max<float>(1.0f, 0.06f * fConst0);
		fConst18 = 1.0f / fConst0;
		fConst19 = 0.5f * fConst0;
		fConst20 = 0.055f * fConst0;
		fConst21 = 1.0f / std::tan(219.91148f / fConst0);
		fConst22 = 1.0f - fConst21;
		fConst23 = 1.0f / (fConst21 + 1.0f);
		fConst24 = 1884.9556f / fConst0;
		fConst25 = 3298.6724f / fConst0;
		fConst26 = 7225.663f / fConst0;
		fConst27 = 10053.097f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.14f);
		fHslider1 = FAUSTFLOAT(0.03f);
		fHslider2 = FAUSTFLOAT(0.3f);
		fHslider3 = FAUSTFLOAT(0.08f);
		fHslider4 = FAUSTFLOAT(0.0f);
		fHslider5 = FAUSTFLOAT(0.02f);
		fHslider6 = FAUSTFLOAT(2.2e+02f);
		fHslider7 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec1[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec4[l5] = 0;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec3[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec5[l7] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec12[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec10[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec13[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fVec3[l14] = 0.0f;
		}
		IOTA0 = 0;
		for (int l15 = 0; l15 < 4096; l15 = l15 + 1) {
			fVec4[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fRec14[l16] = 0.0f;
		}
		for (int l17 = 0; l17 < 2; l17 = l17 + 1) {
			fVec5[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fRec7[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 3; l19 = l19 + 1) {
			fRec6[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 3; l20 = l20 + 1) {
			fRec16[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 3; l21 = l21 + 1) {
			fRec17[l21] = 0.0f;
		}
		for (int l22 = 0; l22 < 3; l22 = l22 + 1) {
			fRec18[l22] = 0.0f;
		}
		for (int l23 = 0; l23 < 3; l23 = l23 + 1) {
			fRec19[l23] = 0.0f;
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
	
	virtual SaxReed* clone() {
		return new SaxReed();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("sax_reed");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.03f), FAUSTFLOAT(0.005f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("breath", &fHslider3, FAUSTFLOAT(0.08f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.3f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bright", &fHslider2, FAUSTFLOAT(0.3f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider6, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider7, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("growl", &fHslider4, FAUSTFLOAT(0.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("release", &fHslider0, FAUSTFLOAT(0.14f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("vibrato", &fHslider5, FAUSTFLOAT(0.02f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.06f), FAUSTFLOAT(0.0001f));
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
		float fSlow5 = float(fHslider2);
		float fSlow6 = std::tan(fConst5 * (1.5e+03f * fSlow5 + 2e+03f));
		float fSlow7 = 2.0f * (1.0f - 1.0f / SaxReed_faustpower2_f(fSlow6));
		float fSlow8 = 1.0f / fSlow6;
		float fSlow9 = (fSlow8 + -0.5555556f) / fSlow6 + 1.0f;
		float fSlow10 = (fSlow8 + 0.5555556f) / fSlow6 + 1.0f;
		float fSlow11 = 1.0f / fSlow10;
		float fSlow12 = float(fHslider3) / (fSlow6 * fSlow10);
		float fSlow13 = float(fHslider4);
		float fSlow14 = 1.3969839e-10f * fSlow13;
		float fSlow15 = std::tan(fConst5 * (3.4e+03f * fSlow5 + 3.2e+03f));
		float fSlow16 = 2.0f * (1.0f - 1.0f / SaxReed_faustpower2_f(fSlow15));
		float fSlow17 = 1.0f / fSlow15;
		float fSlow18 = (fSlow17 + -1.4142135f) / fSlow15 + 1.0f;
		float fSlow19 = (fSlow17 + 1.4142135f) / fSlow15 + 1.0f;
		float fSlow20 = 1.0f / fSlow19;
		float fSlow21 = 0.28f * fSlow13;
		float fSlow22 = float(fHslider5);
		float fSlow23 = float(fHslider6);
		float fSlow24 = 2.0f * fSlow23;
		float fSlow25 = 0.18f * fSlow13;
		float fSlow26 = 0.5f * fSlow23;
		float fSlow27 = 4.0f * fSlow13 + 1.0f;
		float fSlow28 = 0.3f / fSlow19;
		float fSlow29 = 0.66f * fSlow5 + 0.82f;
		float fSlow30 = std::tan(fConst24 * fSlow29);
		float fSlow31 = 2.0f * (1.0f - 1.0f / SaxReed_faustpower2_f(fSlow30));
		float fSlow32 = 1.0f / fSlow30;
		float fSlow33 = (fSlow32 + -0.41666666f) / fSlow30 + 1.0f;
		float fSlow34 = (fSlow32 + 0.41666666f) / fSlow30 + 1.0f;
		float fSlow35 = 1.0f / fSlow34;
		float fSlow36 = 0.7f / (fSlow30 * fSlow34);
		float fSlow37 = std::tan(fConst25 * fSlow29);
		float fSlow38 = 2.0f * (1.0f - 1.0f / SaxReed_faustpower2_f(fSlow37));
		float fSlow39 = 1.0f / fSlow37;
		float fSlow40 = (fSlow39 + -0.35714287f) / fSlow37 + 1.0f;
		float fSlow41 = (fSlow39 + 0.35714287f) / fSlow37 + 1.0f;
		float fSlow42 = 1.0f / fSlow41;
		float fSlow43 = 1.2f / (fSlow37 * fSlow41);
		float fSlow44 = std::tan(fConst26 * fSlow29);
		float fSlow45 = 2.0f * (1.0f - 1.0f / SaxReed_faustpower2_f(fSlow44));
		float fSlow46 = 1.0f / fSlow44;
		float fSlow47 = (fSlow46 + -0.29411766f) / fSlow44 + 1.0f;
		float fSlow48 = (fSlow46 + 0.29411766f) / fSlow44 + 1.0f;
		float fSlow49 = 1.0f / fSlow48;
		float fSlow50 = 1.05f / (fSlow44 * fSlow48);
		float fSlow51 = std::tan(fConst27 * fSlow29);
		float fSlow52 = 2.0f * (1.0f - 1.0f / SaxReed_faustpower2_f(fSlow51));
		float fSlow53 = 1.0f / fSlow51;
		float fSlow54 = (fSlow53 + -0.23809524f) / fSlow51 + 1.0f;
		float fSlow55 = (fSlow53 + 0.23809524f) / fSlow51 + 1.0f;
		float fSlow56 = 1.0f / fSlow55;
		float fSlow57 = (0.6f * fSlow13 + 0.65f) / (fSlow51 * fSlow55);
		float fSlow58 = 0.3f * float(fHslider7);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iVec1[0] = 1;
			iRec0[0] = (iRec0[1] + (iRec0[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec0[0]);
			iRec1[0] = iSlow1 * (iRec1[1] + 1);
			float fTemp1 = float(iRec1[0]);
			fRec2[0] = fSlow0 + fRec2[1] * float(fVec0[1] >= fSlow0);
			float fTemp2 = std::max<float>(0.0f, std::min<float>(fSlow4 * fRec2[0], std::max<float>(fConst4 * (fSlow3 - fRec2[0]) + 1.0f, 0.82f)) * (1.0f - fSlow2 * fTemp1));
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			float fTemp3 = float(iRec4[0]);
			fRec3[0] = 4.656613e-10f * fTemp3 - fSlow11 * (fSlow9 * fRec3[2] + fSlow7 * fRec3[1]);
			fRec5[0] = fSlow14 * fTemp3 - fConst11 * (fConst9 * fRec5[2] + fConst7 * fRec5[1]);
			int iTemp4 = 1 - iVec1[1];
			float fTemp5 = ((iTemp4) ? 0.0f : fConst13 + fRec9[1]);
			fRec9[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = ((iTemp4) ? 0.0f : fConst14 + fRec12[1]);
			fRec12[0] = fTemp6 - std::floor(fTemp6);
			float fTemp7 = (0.055f * std::max<float>(0.0f, std::min<float>(fConst17 * fRec2[0], 1.0f) - fConst17 * fTemp1) + 0.945f) * (fSlow22 * std::max<float>(0.0f, std::min<float>(fConst16 * fRec2[0], 1.0f) - fConst15 * fTemp1) * ftbl0SaxReedSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec12[0]), 65535))] + 1.0f);
			float fTemp8 = std::max<float>(1.1920929e-07f, std::fabs(fSlow24 * fTemp7));
			float fTemp9 = fRec10[1] + fConst18 * fTemp8;
			float fTemp10 = fTemp9 + -1.0f;
			int iTemp11 = fTemp10 < 0.0f;
			fRec10[0] = ((iTemp11) ? fTemp9 : fTemp10);
			float fRec11 = ((iTemp11) ? fTemp9 : fTemp9 + fTemp10 * (1.0f - fConst0 / fTemp8));
			float fTemp12 = std::max<float>(fSlow26 * fTemp7, 23.44895f);
			float fTemp13 = std::max<float>(2e+01f, std::fabs(fTemp12));
			float fTemp14 = ((iTemp4) ? 0.0f : fRec13[1] + fConst18 * fTemp13);
			fRec13[0] = fTemp14 - std::floor(fTemp14);
			float fTemp15 = SaxReed_faustpower2_f(2.0f * fRec13[0] + -1.0f);
			fVec3[0] = fTemp15;
			float fTemp16 = float(iVec1[1]) * (fTemp15 - fVec3[1]) / fTemp13;
			fVec4[IOTA0 & 4095] = fTemp16;
			float fTemp17 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst19 / fTemp12));
			int iTemp18 = int(fTemp17);
			float fTemp19 = std::floor(fTemp17);
			float fTemp20 = std::max<float>(1.1920929e-07f, std::fabs(fSlow23 * fTemp7));
			float fTemp21 = fRec14[1] + fConst18 * fTemp20;
			float fTemp22 = fTemp21 + -1.0f;
			int iTemp23 = fTemp22 < 0.0f;
			fRec14[0] = ((iTemp23) ? fTemp21 : fTemp22);
			float fRec15 = ((iTemp23) ? fTemp21 : fTemp21 + fTemp22 * (1.0f - fConst0 / fTemp20));
			float fTemp24 = tanhf(fSlow27 * (2.0f * fRec15 + fConst20 * (fTemp16 - fVec4[(IOTA0 - iTemp18) & 4095] * (fTemp19 + (1.0f - fTemp17)) - (fTemp17 - fTemp19) * fVec4[(IOTA0 - (iTemp18 + 1)) & 4095]) + fSlow25 * (2.0f * fRec11 + -1.0f) + -1.0f) * (fSlow21 * ftbl0SaxReedSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec9[0]), 65535))] + 1.0f));
			fVec5[0] = fTemp24;
			fRec7[0] = -(fConst23 * (fConst22 * fRec7[1] - fConst21 * (fTemp24 - fVec5[1])));
			fRec6[0] = fRec7[0] - fSlow20 * (fSlow18 * fRec6[2] + fSlow16 * fRec6[1]);
			float fTemp25 = fRec6[2] + fRec6[0] + 2.0f * fRec6[1];
			float fTemp26 = fSlow20 * fTemp25;
			fRec16[0] = fTemp26 - fSlow35 * (fSlow33 * fRec16[2] + fSlow31 * fRec16[1]);
			fRec17[0] = fTemp26 - fSlow42 * (fSlow40 * fRec17[2] + fSlow38 * fRec17[1]);
			fRec18[0] = fTemp26 - fSlow49 * (fSlow47 * fRec18[2] + fSlow45 * fRec18[1]);
			fRec19[0] = fTemp26 - fSlow56 * (fSlow54 * fRec19[2] + fSlow52 * fRec19[1]);
			float fTemp27 = fSlow58 * (1.5f * (0.34f * (fSlow57 * (fRec19[0] - fRec19[2]) + fSlow50 * (fRec18[0] - fRec18[2]) + fSlow43 * (fRec17[0] - fRec17[2]) + fSlow36 * (fRec16[0] - fRec16[2]) + fSlow28 * fTemp25) + fConst12 * (fRec5[0] - fRec5[2])) * fTemp2 + fSlow12 * (fRec3[0] - fRec3[2]) * (0.45f * fTemp2 + 1.4f * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fConst3 * (fConst1 - fTemp0) + 1.0f))));
			output0[i0] = FAUSTFLOAT(fTemp27);
			output1[i0] = FAUSTFLOAT(fTemp27);
			fVec0[1] = fVec0[0];
			iVec1[1] = iVec1[0];
			iRec0[1] = iRec0[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			iRec4[1] = iRec4[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
			fRec9[1] = fRec9[0];
			fRec12[1] = fRec12[0];
			fRec10[1] = fRec10[0];
			fRec13[1] = fRec13[0];
			fVec3[1] = fVec3[0];
			IOTA0 = IOTA0 + 1;
			fRec14[1] = fRec14[0];
			fVec5[1] = fVec5[0];
			fRec7[1] = fRec7[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec16[2] = fRec16[1];
			fRec16[1] = fRec16[0];
			fRec17[2] = fRec17[1];
			fRec17[1] = fRec17[0];
			fRec18[2] = fRec18[1];
			fRec18[1] = fRec18[0];
			fRec19[2] = fRec19[1];
			fRec19[1] = fRec19[0];
		}
	}

};

#endif
